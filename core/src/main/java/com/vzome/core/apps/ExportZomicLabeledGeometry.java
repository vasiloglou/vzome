package com.vzome.core.apps;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.vzome.core.algebra.AlgebraicField;
import com.vzome.core.algebra.AlgebraicNumber;
import com.vzome.core.algebra.AlgebraicVector;
import com.vzome.core.algebra.PentagonField;
import com.vzome.core.commands.ZomicVirtualMachine;
import com.vzome.core.construction.Color;
import com.vzome.core.construction.Construction;
import com.vzome.core.construction.ConstructionChanges;
import com.vzome.core.construction.FreePoint;
import com.vzome.core.construction.Point;
import com.vzome.core.construction.Segment;
import com.vzome.core.math.symmetry.IcosahedralSymmetry;
import com.vzome.core.zomic.Interpreter;
import com.vzome.core.zomic.ZomicASTCompiler;
import com.vzome.core.zomic.ZomicException;
import com.vzome.core.zomic.program.Walk;


public final class ExportZomicLabeledGeometry
{
    private ExportZomicLabeledGeometry()
    {
    }

    private static final class RecordingConstructions implements ConstructionChanges
    {
        private final List<Map<String, Object>> segments = new ArrayList<>();

        private final Set<String> segmentSignatures = new LinkedHashSet<>();

        @Override
        public void constructionAdded( Construction construction )
        {
            record( construction );
        }

        @Override
        public void constructionAdded( Construction construction, Color color )
        {
            record( construction );
        }

        private void record( Construction construction )
        {
            if ( ! ( construction instanceof Segment ) || construction .isImpossible() )
                return;
            Segment segment = (Segment) construction;
            String signature = segment .getSignature();
            if ( this .segmentSignatures .add( signature ) )
                this .segments .add( segmentMap( segment ) );
        }
    }

    private static final class RecordingVirtualMachine extends ZomicVirtualMachine
    {
        RecordingVirtualMachine( Point start, ConstructionChanges effects, IcosahedralSymmetry symmetry )
        {
            super( start, effects, symmetry );
        }

        AlgebraicVector currentLocation()
        {
            return this .getLocation();
        }
    }

    private static final class LabelCapturingInterpreter extends Interpreter
    {
        private final RecordingVirtualMachine vm;

        private final List<Map<String, Object>> labeledPoints;

        private final Map<String, Integer> labelOccurrences = new LinkedHashMap<>();

        LabelCapturingInterpreter(
            RecordingVirtualMachine vm,
            IcosahedralSymmetry symmetry,
            List<Map<String, Object>> labeledPoints )
        {
            super( vm, symmetry );
            this .vm = vm;
            this .labeledPoints = labeledPoints;
        }

        @Override
        public void visitLabel( String id )
        {
            int occurrence = this .labelOccurrences .merge( id, 1, Integer::sum );
            this .labeledPoints .add( labeledPointMap( id, occurrence, this .vm .currentLocation() ) );
        }
    }

    public static Map<String, Object> exportLabeledGeometry( File zomicFile )
        throws IOException, ZomicException
    {
        PentagonField field = new PentagonField();
        IcosahedralSymmetry symmetry = new IcosahedralSymmetry( field );
        Walk program = ZomicASTCompiler .compile( zomicFile, symmetry );
        if ( program == null )
            throw new IllegalArgumentException( "Zomic compiler returned null for " + zomicFile );
        if ( program .getErrors() != null && program .getErrors() .length > 0 )
            throw new IllegalArgumentException( program .getErrors()[ 0 ] );

        RecordingConstructions effects = new RecordingConstructions();
        RecordingVirtualMachine vm = new RecordingVirtualMachine(
            new FreePoint( field .origin( 3 ) ),
            effects,
            symmetry
        );
        List<Map<String, Object>> labeledPoints = new ArrayList<>();
        LabelCapturingInterpreter interpreter = new LabelCapturingInterpreter( vm, symmetry, labeledPoints );
        program .accept( interpreter );

        Map<String, Object> result = new LinkedHashMap<>();
        result .put( "zomic_file", zomicFile .getAbsolutePath() );
        result .put( "parser", "antlr4" );
        result .put( "symmetry", "icosahedral" );
        result .put( "labeled_points", labeledPoints );
        result .put( "segments", effects .segments );
        return result;
    }

    private static Map<String, Object> labeledPointMap( String label, int occurrence, AlgebraicVector location )
    {
        Map<String, Object> result = new LinkedHashMap<>();
        result .put( "label", occurrence == 1 ? label : label + "#" + occurrence );
        result .put( "source_label", label );
        result .put( "occurrence", occurrence );
        result .put( "position", vectorMap( location ) );
        result .put( "cartesian", Arrays .stream( location .projectTo3d( true ) .to3dDoubleVector() )
            .boxed()
            .toList() );
        return result;
    }

    private static Map<String, Object> segmentMap( Segment segment )
    {
        Map<String, Object> result = new LinkedHashMap<>();
        result .put( "signature", segment .getSignature() );
        result .put( "start", vectorMap( segment .getStart() ) );
        result .put( "end", vectorMap( segment .getEnd() ) );
        return result;
    }

    private static Map<String, Object> vectorMap( AlgebraicVector vector )
    {
        AlgebraicVector projected = vector .projectTo3d( true );
        Map<String, Object> result = new LinkedHashMap<>();
        result .put( "zomic_expression", projected .toString( AlgebraicField .ZOMIC_FORMAT ) );
        result .put( "expression", projected .toString( AlgebraicField .EXPRESSION_FORMAT ) );

        List<Map<String, Object>> components = new ArrayList<>();
        for ( int i = 0; i < 3; i++ ) {
            components .add( numberMap( projected .getComponent( i ) ) );
        }
        result .put( "components", components );
        return result;
    }

    private static Map<String, Object> numberMap( AlgebraicNumber number )
    {
        Map<String, Object> result = new LinkedHashMap<>();
        result .put( "expression", number .toString( AlgebraicField .EXPRESSION_FORMAT ) );
        result .put( "zomic_expression", number .toString( AlgebraicField .ZOMIC_FORMAT ) );
        result .put( "trailing_divisor", number .toTrailingDivisor() );
        result .put( "evaluate", number .evaluate() );
        return result;
    }

    public static void main( String[] args )
        throws Exception
    {
        if ( args .length != 2 ) {
            System.err.println( "Usage: ExportZomicLabeledGeometry <zomic-file> <output-json>" );
            System.exit( 2 );
        }

        File zomicFile = new File( args[ 0 ] );
        File outputFile = new File( args[ 1 ] );
        File outputDir = outputFile .getAbsoluteFile() .getParentFile();
        if ( outputDir != null && ! outputDir .isDirectory() && ! outputDir .mkdirs() ) {
            throw new IOException( "unable to create output directory: " + outputDir );
        }

        Map<String, Object> result = exportLabeledGeometry( zomicFile );
        ObjectMapper mapper = new ObjectMapper()
            .enable( SerializationFeature .INDENT_OUTPUT );
        mapper .writeValue( outputFile, result );
    }
}
